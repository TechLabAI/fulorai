import { ComponentFixture, TestBed } from '@angular/core/testing';
import { LeadUiComponent } from './lead-ui.component';

describe('LeadUiComponent', () => {
  let component: LeadUiComponent;
  let fixture: ComponentFixture<LeadUiComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LeadUiComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(LeadUiComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
