import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CommNavigationComponent } from './comm-navigation.component';

describe('CommNavigationComponent', () => {
  let component: CommNavigationComponent;
  let fixture: ComponentFixture<CommNavigationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CommNavigationComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(CommNavigationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
