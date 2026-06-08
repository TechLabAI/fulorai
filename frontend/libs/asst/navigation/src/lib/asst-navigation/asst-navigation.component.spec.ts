import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AsstNavigationComponent } from './asst-navigation.component';

describe('AsstNavigationComponent', () => {
  let component: AsstNavigationComponent;
  let fixture: ComponentFixture<AsstNavigationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AsstNavigationComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(AsstNavigationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
