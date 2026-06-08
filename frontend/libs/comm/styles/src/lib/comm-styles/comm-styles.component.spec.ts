import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CommStylesComponent } from './comm-styles.component';

describe('CommStylesComponent', () => {
  let component: CommStylesComponent;
  let fixture: ComponentFixture<CommStylesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CommStylesComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(CommStylesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
